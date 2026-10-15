package com.vividlands.mixin;

import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Aquifer;
import net.minecraft.world.level.levelgen.DensityFunction;
import net.minecraft.world.level.levelgen.NoiseChunk;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Open-sky shortcut for aquifers. For every non-solid block Minecraft asks the aquifer whether it
 * is water, lava or air, checking up to a dozen nearby aquifer cells. High above the ground and
 * above sea level the answer is always air (local water tables never rise above the land around
 * them), but the full check still ran for every sky block - a fifth of generation time in a
 * 576-block-tall world. Answer air at once there; everything at or near the surface is unchanged.
 */
@Mixin(Aquifer.NoiseBasedAquifer.class)
public abstract class NoiseBasedAquiferMixin {
    @Shadow
    @Final
    private NoiseChunk noiseChunk;

    @Shadow
    @Final
    private Aquifer.FluidPicker globalFluidPicker;

    @Shadow
    private boolean shouldScheduleFluidUpdate;

    @Inject(method = "computeSubstance", at = @At("HEAD"), cancellable = true)
    private void vividlands$openSky(DensityFunction.FunctionContext ctx, double density,
                                    CallbackInfoReturnable<BlockState> cir) {
        if (density > 0.0) {
            return;                                         // solid: vanilla handles it
        }
        int x = ctx.blockX(), y = ctx.blockY(), z = ctx.blockZ();
        if (y <= this.noiseChunk.preliminarySurfaceLevel(x, z) + 16) {
            return;                                         // near or below the ground: full check
        }
        if (!this.globalFluidPicker.computeFluid(x, y, z).at(y).isAir()) {
            return;                                         // below sea level (open water): full check
        }
        this.shouldScheduleFluidUpdate = false;
        cir.setReturnValue(Blocks.AIR.defaultBlockState());
    }
}
