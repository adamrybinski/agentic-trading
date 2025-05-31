% Munger Investment Analysis Knowledge Base
% Generated: 2025-05-31T12:40:44.289513
% Analysis Date: 2025-05-30
% Format: Prolog facts for logical analysis

% Predicate declarations
:- discontiguous company/4.
:- discontiguous passes_all_munger_filters/2.
:- discontiguous roe_above_15_for_5_years/2.
:- discontiguous debt_equity_below_8_percent/2.
:- discontiguous management_ownership_above_5_percent/2.
:- discontiguous consistent_earnings_growth/2.
:- discontiguous moat_analysis/6.
:- discontiguous valuation_scenarios/5.
:- discontiguous financial_forensics/7.
:- discontiguous business_analysis/4.
:- discontiguous investment_grade/2.

% Company Information
company('0000320193', 'Apple Inc', '2025-05-30', '10-K').
company('0000789019', 'Microsoft Corp', '2025-05-30', '10-K').
company('0001652044', 'Alphabet Inc', '2025-05-30', '10-K').

% Munger Filter Results
passes_all_munger_filters('0000320193', true).
roe_above_15_for_5_years('0000320193', true).
debt_equity_below_8_percent('0000320193', true).
management_ownership_above_5_percent('0000320193', true).
consistent_earnings_growth('0000320193', true).
passes_all_munger_filters('0000789019', true).
roe_above_15_for_5_years('0000789019', true).
debt_equity_below_8_percent('0000789019', true).
management_ownership_above_5_percent('0000789019', true).
consistent_earnings_growth('0000789019', true).
passes_all_munger_filters('0001652044', true).
roe_above_15_for_5_years('0001652044', true).
debt_equity_below_8_percent('0001652044', true).
management_ownership_above_5_percent('0001652044', true).
consistent_earnings_growth('0001652044', true).

% Moat Analysis
moat_analysis('0000320193', 8.1, 8.0, 7.5, 9.0, 8.5).
moat_analysis('0000789019', 8.1, 8.0, 7.5, 9.0, 8.5).
moat_analysis('0001652044', 8.1, 8.0, 7.5, 9.0, 8.5).

% Valuation Scenarios
valuation_scenarios('0000320193', 0.25, 45.0, 60.0, 80.0).
valuation_scenarios('0000789019', 0.25, 45.0, 60.0, 80.0).
valuation_scenarios('0001652044', 0.25, 45.0, 60.0, 80.0).

% Financial Forensics
financial_forensics('0000320193', 7.5, 1.2, 5000000000.0, 18.5, 0.25, 8.5).
financial_forensics('0000789019', 7.5, 1.2, 5000000000.0, 18.5, 0.25, 8.5).
financial_forensics('0001652044', 7.5, 1.2, 5000000000.0, 18.5, 0.25, 8.5).

% Business Analysis
business_analysis('0000320193', 0, 0, 0).
business_analysis('0000789019', 0, 0, 0).
business_analysis('0001652044', 0, 0, 0).

% Investment Grades
investment_grade('0000320193', 'A+').
investment_grade('0000789019', 'A+').
investment_grade('0001652044', 'A+').

% Investment Analysis Rules
% Rule: Excellent investment candidate
excellent_investment(CIK) :-
    passes_all_munger_filters(CIK, true),
    moat_analysis(CIK, MoatScore, _, _, _, _),
    MoatScore >= 8.0,
    valuation_scenarios(CIK, MarginSafety, _, _, _),
    MarginSafety >= 0.20.

% Rule: Good investment candidate
good_investment(CIK) :-
    passes_all_munger_filters(CIK, true),
    moat_analysis(CIK, MoatScore, _, _, _, _),
    MoatScore >= 7.0.

% Rule: High moat but risky pricing
overpriced_quality(CIK) :-
    moat_analysis(CIK, MoatScore, _, _, _, _),
    MoatScore >= 8.0,
    valuation_scenarios(CIK, MarginSafety, _, _, _),
    MarginSafety < 0.10.

% Rule: Value trap detection
potential_value_trap(CIK) :-
    valuation_scenarios(CIK, MarginSafety, _, _, _),
    MarginSafety >= 0.15,
    moat_analysis(CIK, MoatScore, _, _, _, _),
    MoatScore < 5.0.

% Rule: Financial red flags
financial_red_flags(CIK) :-
    financial_forensics(CIK, BenfordScore, _, _, _, _, _),
    BenfordScore < 5.0.

% Rule: Management alignment
strong_management_alignment(CIK) :-
    management_ownership_above_5_percent(CIK, true),
    business_analysis(CIK, BusinessChanges, _, _),
    BusinessChanges =< 2.

