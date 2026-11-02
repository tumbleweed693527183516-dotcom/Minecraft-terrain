package com.vividlands.ragnarok.mixin;

import com.vividlands.ragnarok.classes.Classes;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Class passives and marks change how much damage a hit does (Classes.outgoing). */
@Mixin(LivingEntity.class)
public abstract class ClassDamageMixin {
    @ModifyVariable(method = "hurt", at = @At("HEAD"), argsOnly = true, ordinal = 0)
    private float vlr$classDamage(float amount, DamageSource source, float original) {
        return Classes.outgoing((LivingEntity) (Object) this, source, amount);
    }
}
