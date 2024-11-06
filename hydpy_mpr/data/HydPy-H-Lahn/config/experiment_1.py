from hydpy.models.hland.hland_control import FC
from hydpy_mpr import Config, RasterTask

import calibrators
import coefficients
import equations
import upscalers
import transformers

config = Config(
    calibrator=calibrators.MyCalibrator,
    tasks=[
        RasterTask(
            equation=equations.FC(
                dir_group="raster_5km",
                file_sand="sand_mean_0_200_res5km",
                file_clay="clay_mean_0_200_res5km",
                coef_const=coefficients.coef_const,
                coef_factor_sand=coefficients.coef_factor_sand,
                coef_factor_clay=coefficients.coef_factor_clay,
            ),
            upscaler=upscalers.RasterMean,
            transformers=[transformers.RasterIdentityTransformer(hland_96=FC)],
        )
    ],
    subequations=[equations.KS],
)
