from hydpy.models.hland import hland_control
import hydpy_mpr as mpr

import calibrators
import coefficients
import equations
import initialisers
import upscalers
import transformers

config = mpr.Config(
    hp=initialisers.initialise_lahn(),
    tasks=[
        mpr.RasterTask(
            equation=equations.FC(
                dir_group="raster_5km",
                file_sand="sand_mean_0_200_res5km",
                file_clay="clay_mean_0_200_res5km",
                coef_const=coefficients.coef_const,
                coef_factor_sand=coefficients.coef_factor_sand,
                coef_factor_clay=coefficients.coef_factor_clay,
            ),
            upscaler=upscalers.RasterMean(),
            transformers=[
                transformers.RasterIdentityTransformer(hland_96=hland_control.FC)
            ],
        )
    ],
    calibrator=calibrators.MyCalibrator(),
    runner=mpr.Runner(),
    writers=[mpr.ControlWriter(controldir="experiment_1")],
)


if __name__ == "__main__":
    config.runner.run(maxeval=100)
