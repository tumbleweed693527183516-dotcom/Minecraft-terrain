package com.vividlands.ragnarok.mixin;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.portal.PortalShape;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.Optional;
import java.util.function.Predicate;

/** The Nether is closed: an obsidian frame never becomes a portal (the fire is just fire). */
@Mixin(PortalShape.class)
public abstract class PortalShapeMixin {
    @Inject(method = "findPortalShape", at = @At("HEAD"), cancellable = true)
    private static void ragnarok$noNetherPortal(LevelAccessor level, BlockPos pos, Predicate<PortalShape> predicate,
                                                Direction.Axis axis, CallbackInfoReturnable<Optional<PortalShape>> cir) {
        cir.setReturnValue(Optional.empty());
    }
}
