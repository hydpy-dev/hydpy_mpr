import os

from hydpy.models.hland import hland_control
import hydpy_mpr

import calibrators
import coefficients
import initialisers
import regionalisers

mpr = hydpy_mpr.MPR(
    mprpath=os.path.join("HydPy-H-Lahn", "mpr_data"),
    hp=initialisers.initialise_lahn(),
    # preprocessor=[
    #     RasterConverter(inputrasters=..., outputraster...)
    # ],
    tasks=[
        hydpy_mpr.RasterSubunitTask(
            regionaliser=regionalisers.FC2m(
                source="raster_15km",
                source_clay="clay_mean_0_200_res15km_pct",
                source_density="bdod_mean_0_200_res15km_gcm3",
                coef_const=coefficients.fc_const,
                coef_factor_clay=coefficients.fc_clay,
                coef_factor_density=coefficients.fc_density,
            ),
            upscaler=hydpy_mpr.RasterSubunitDefaultUpscaler(),
            transformers=[
                hydpy_mpr.SubunitIdentityTransformer(
                    parameter=hland_control.FC, model="hland_96"
                )
            ],
        )
    ],
    calibrator=calibrators.MyCalibrator(maxeval=100),
    writers=[hydpy_mpr.ControlWriter(controldir="calibrated")],
)


if __name__ == "__main__":
    mpr.run()
