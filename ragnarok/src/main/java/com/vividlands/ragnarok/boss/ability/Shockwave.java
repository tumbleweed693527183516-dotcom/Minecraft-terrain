package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;

import java.util.HashSet;
import java.util.Set;

/** A ring that rolls outward along the ground; jump over it as it passes or be thrown into the air. */
public class Shockwave extends Ability {
    private final int windup;
    private final double maxRadius, speed, damageMul;
    private final Set<LivingEntity> hit = new HashSet<>();

    public Shockwave(int cooldown, int windup, double maxRadius, double speed, double damageMul) {
        super(cooldown);
        this.windup = windup;
        this.maxRadius = maxRadius;
        this.speed = speed;
        this.damageMul = damageMul;
        range(0, maxRadius * 0.9);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        hit.clear();
        f.mob().playAmbientSound();
        return windup + (int) Math.ceil(maxRadius / speed) + 2;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        if (t < windup) {
            f.face(target);
            return;
        }
        if (t == windup) f.sound(SoundEvents.GENERIC_EXPLODE, 1.5f, 0.4f);
        double r = (t - windup) * speed + f.mob().getBbWidth() * 0.5;
        int points = (int) Math.min(64, 8 + r * 5);
        f.groundRing(r, points);
        if (t % 2 == 0) {
            for (int i = 0; i < points / 2; i++) {
                double a = Math.PI * 2 * i / (points / 2.0);
                f.particles(ParticleTypes.POOF, f.mob().getX() + Math.cos(a) * r, f.mob().getY() + 0.2,
                        f.mob().getZ() + Math.sin(a) * r, 1, 0, 0.05, 0, 0.01);
            }
        }
        for (LivingEntity e : f.victims(r + 1)) {
            double d = f.horizontalDistance(e);
            if (Math.abs(d - r) > 1.2 || !e.onGround() || hit.contains(e)) continue;
            hit.add(e);
            if (f.hurt(e, (float) (f.attackDamage() * damageMul))) f.push(e, 0.5, 0.9);
        }
    }
}
