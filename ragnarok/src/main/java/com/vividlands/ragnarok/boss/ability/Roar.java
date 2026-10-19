package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;

import java.util.List;
import java.util.function.Supplier;

/** Rears up and roars: everything close gets the effects (slowed, weakened, stunned) and is pushed back. */
public class Roar extends Ability {
    private final double radius;
    private final int windup;
    private final double push;
    private final SoundEvent sound;
    private final float pitch;
    private final List<Supplier<MobEffectInstance>> effects;

    @SafeVarargs
    public Roar(int cooldown, double radius, int windup, double push, SoundEvent sound, float pitch, Supplier<MobEffectInstance>... effects) {
        super(cooldown);
        this.radius = radius;
        this.windup = windup;
        this.push = push;
        this.sound = sound;
        this.pitch = pitch;
        this.effects = List.of(effects);
        range(0, radius);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.mob().playAmbientSound();
        return windup + 12;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t == windup) {
            f.sound(sound, 3f, pitch);
            var m = f.mob();
            for (int i = 0; i < 3; i++) {
                f.particles(ParticleTypes.SONIC_BOOM, m.getX(), m.getEyeY(), m.getZ(), 1, 0, 0, 0, 0);
            }
            f.particles(ParticleTypes.CLOUD, m.getX(), m.getY() + 0.5, m.getZ(), 40, radius * 0.4, 0.3, radius * 0.4, 0.15);
            for (LivingEntity e : f.victims(radius)) {
                for (var s : effects) f.effect(e, s.get());
                if (push > 0) f.push(e, push, 0.3);
            }
        }
    }
}
