package com.vividlands.ragnarok.mixin;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.SculkShriekerBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** No Warden: shriekers never summon one. */
@Mixin(SculkShriekerBlockEntity.class)
public abstract class SculkShriekerMixin {
    @Inject(method = "trySummonWarden", at = @At("HEAD"), cancellable = true)
    private void ragnarok$noWarden(ServerLevel level, CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(false);
    }
}
