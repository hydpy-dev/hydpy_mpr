from hydpy.models.hland import hland_control
import hydpy_mpr

import calibrators
import coefficients
import equations
import initialisers
import upscalers
import transformers

mpr = hydpy_mpr.MPR(
    hp=initialisers.initialise_lahn(),
    tasks=[
        hydpy_mpr.RasterTask(
            equation=equations.FC(
                dir_group="raster_5km",
                file_sand="sand_mean_0_200_res5km",
                file_clay="clay_mean_0_200_res5km",
                coef_const=coefficients.coef_const,
                coef_factor_sand=coefficients.coef_factor_sand,
                coef_factor_clay=coefficients.coef_factor_clay,
            ),
            upscaler=upscalers.RasterElementMean(),
            transformers=[
                transformers.RasterIdentityTransformer(hland_96=hland_control.FC)
            ],
        )
    ],
    calibrator=calibrators.MyCalibrator(maxeval=100),
    writers=[hydpy_mpr.ControlWriter(controldir="experiment_1")],
)


if __name__ == "__main__":
    mpr.run()
