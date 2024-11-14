import hydpy_mpr


fc_const = hydpy_mpr.Coefficient(name="fc_const", default=20.0, lower=5.0, upper=50.0)
fc_clay = hydpy_mpr.Coefficient(
    name="fc_factor_clay", default=0.5, lower=0.0, upper=1.0
)
fc_density = hydpy_mpr.Coefficient(
    name="fc_factor_density", default=-1.0, lower=-5.0, upper=0.0
)

beta_density = hydpy_mpr.Coefficient(
    name="beta_factor_density", default=2.0, lower=1.0, upper=3.0
)
