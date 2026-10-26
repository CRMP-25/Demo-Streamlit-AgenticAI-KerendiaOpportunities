"""V7.7.8 participant-level, design-aware screening-proxy estimation.

Only analyzes user-supplied authentic microdata/derived flags; never fabricates inputs.
The user must establish cohort, screening definitions, weights and survey cycle.
Taylor linearization assumes independent with-replacement PSUs within strata.
"""
from __future__ import annotations
import math
import pandas as pd
from scipy.stats import t as student_t


class SurveyInputError(ValueError):
    pass


def compute_screening_total(frame: pd.DataFrame, *, flag: str, weight: str,
                            strata: str, psu: str, universe: str | None = None) -> dict:
    required = [flag, weight, strata, psu] + ([universe] if universe else [])
    if len(set(required)) != len(required):
        raise SurveyInputError('Each mapping must use a distinct column.')
    missing = [col for col in required if col not in frame.columns]
    if missing:
        raise SurveyInputError('Missing mapped columns: ' + ', '.join(missing))
    if len(frame) == 0:
        raise SurveyInputError('The uploaded dataset is empty.')
    data = frame[required].copy()
    if universe:
        eligible = pd.to_numeric(data[universe], errors='coerce')
        if not eligible.dropna().isin([0, 1]).all():
            raise SurveyInputError('Universe flag must contain only 0, 1 or missing values.')
        # Excluded rows remain as zeros for total estimation within the supplied sample design.
        data['_in_universe'] = eligible.eq(1)
    else:
        data['_in_universe'] = True
    f = pd.to_numeric(data[flag], errors='coerce')
    w = pd.to_numeric(data[weight], errors='coerce')
    if not f.dropna().isin([0, 1]).all():
        raise SurveyInputError('Screening flag must contain only 0, 1 or missing values.')
    if (w.dropna() < 0).any() or not w.notna().all() or not w.map(math.isfinite).all():
        raise SurveyInputError('All survey weights must be finite and nonnegative.')
    if (data[strata].isna() | data[psu].isna()).any():
        raise SurveyInputError('Strata and PSU values must be present for every record.')
    valid = data['_in_universe'] & f.notna()
    # Explicit complete-case handling: missing screening values contribute zero;
    # the missing-weight fraction is reported, not silently treated as negative.
    data['_y'] = w * f.fillna(0) * data['_in_universe'].astype(float)
    data['_denom'] = w * valid.astype(float)
    data['_missing_weight'] = w * (data['_in_universe'] & f.isna()).astype(float)
    data['_universe_weight'] = w * data['_in_universe'].astype(float)
    total = float(data['_y'].sum())
    denom = float(data['_denom'].sum())
    if denom <= 0:
        raise SurveyInputError('No positive-weight observations with known screening status in the universe.')
    count = int((valid & f.eq(1)).sum())
    known = int(valid.sum())
    missing_count = int((data['_in_universe'] & f.isna()).sum())
    # Within-stratum variance of PSU totals: m/(m-1) * sum((t_j - mean)^2).
    # Conservative single-PSU handling: no CI rather than falsely reporting zero variance.
    psu_totals = data.groupby([strata, psu], dropna=False)['_y'].sum()
    variance = 0.0
    singleton = []
    df = 0
    for stratum, vals in psu_totals.groupby(level=0, sort=False):
        arr = vals.to_numpy(dtype=float)
        m = len(arr)
        if m < 2:
            singleton.append(str(stratum))
            continue
        variance += float(m / (m - 1) * ((arr - arr.mean()) ** 2).sum())
        df += m - 1
    se = math.sqrt(max(variance, 0.0)) if not singleton and df > 0 else None
    # Student-t reference quantile uses estimated design degrees of freedom.
    # This is still an approximate PSU Taylor interval, not a CDC-certified result.
    critical = float(student_t.ppf(0.975, df)) if se is not None else None
    ci_t = [max(0.0, total - critical * se), total + critical * se] if se is not None else None
    ci_normal = [max(0.0, total - 1.96 * se), total + 1.96 * se] if se is not None else None
    missing_weight = float(data['_missing_weight'].sum())
    universe_weight = float(data['_universe_weight'].sum())
    return {
        'status': 'COMPUTED_FROM_UPLOADED_ROWS', 'estimate': total,
        'unweighted_positive': count, 'unweighted_known': known,
        'missing_screening_rows': missing_count,
        'weighted_complete_case_denominator': denom,
        'screening_fraction_among_known': total / denom,
        'standard_error': se, 'ci95_normal_approx': ci_normal,
        'ci95_t_approx': ci_t, 'ci95_t_critical': critical,
        'missing_screening_weight': missing_weight,
        'weighted_universe_total': universe_weight,
        'missing_weight_fraction_in_universe': missing_weight / universe_weight if universe_weight else None,
        'missing_status_sensitivity': {
            'all_missing_negative': total,
            'all_missing_positive': total + missing_weight,
            'interpretation': 'Extreme-case classification bounds holding observed survey weights fixed; not a confidence interval, not a missingness adjustment, and not evidence of clinical eligibility.'
        },
        'design_degrees_freedom': df, 'singleton_strata': singleton,
        'rows_supplied': len(data), 'rows_in_universe': int(data['_in_universe'].sum()),
        'design_method': 'Stratified PSU Taylor variance for weighted total; with-replacement approximation; Student-t CI using PSU design degrees of freedom (normal interval retained for comparison)',
        'limitations': ('Requires verified NHANES cycle weights, appropriate population universe, '
                        'screening flag derivation, missing-data rules, and design variables. '
                        'Not a CKD diagnosis, T2D diagnosis, or finerenone-eligible population. '
                        'Extreme-case missingness bounds are not probability intervals. '
                        'No finite population correction; no multi-cycle weight derivation. '
                        'Singleton strata suppress standard error and CI.'),
    }
