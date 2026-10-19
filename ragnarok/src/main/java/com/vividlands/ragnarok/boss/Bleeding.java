package com.vividlands.ragnarok.boss;

import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import org.joml.Vector3f;

/** Bleeding (saber-tooth fangs, shark teeth): a little damage every second, more at higher levels. */
public class Bleeding extends MobEffect {
    private static final DustParticleOptions BLOOD = new DustParticleOptions(new Vector3f(0.55f, 0.02f, 0.02f), 1.0f);

    public Bleeding() {
        super(MobEffectCategory.HARMFUL, 0x8a0b0b);
    }

    @Override
    public boolean isDurationEffectTick(int duration, int amplifier) {
        return duration % 20 == 0;
    }

    @Override
    public void applyEffectTick(LivingEntity e, int amplifier) {
        e.hurt(e.damageSources().magic(), 1.0f + amplifier);
        if (e.level() instanceof ServerLevel sl) {
            sl.sendParticles(BLOOD, e.getX(), e.getY(0.5), e.getZ(), 6, e.getBbWidth() * 0.3, e.getBbHeight() * 0.25, e.getBbWidth() * 0.3, 0);
        }
    }
}
