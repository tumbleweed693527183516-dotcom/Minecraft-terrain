package com.vividlands.ragnarok.mixin;

import net.minecraft.world.entity.ai.attributes.RangedAttribute;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Vanilla caps max health at 1024, which silently cut every Chapter 2 boss (1200-4000 hp) down to 1024.
 * Raise the cap so the gods get their full health bars.
 */
@Mixin(RangedAttribute.class)
public abstract class MaxHealthCapMixin {
    @Shadow @Final @Mutable private double maxValue;

    @Inject(method = "<init>", at = @At("TAIL"))
    private void vlr$raiseHealthCap(String id, double defaultValue, double min, double max, CallbackInfo ci) {
        if ("attribute.name.generic.max_health".equals(id) && maxValue < 100000) maxValue = 100000;
    }
}
