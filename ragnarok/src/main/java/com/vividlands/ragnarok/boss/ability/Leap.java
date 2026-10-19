package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

import java.util.function.Supplier;

/**
 * Crouches, then leaps at the target (a pounce on land; from the water a lunge or a breach). Hitting the target in
 * mid-air hurts it and applies the effect (bleeding for the saber-tooth and the shark).
 */
public class Leap extends Ability {
    private final int windup;
    private final double damageMul, up;
    private final boolean fromWater;
    private final Supplier<MobEffectInstance> effect;
    private boolean landed, done;

    public Leap(int cooldown, int windup, double min, double max, double damageMul, double up, boolean fromWater,
                Supplier<MobEffectInstance> effect) {
        super(cooldown);
        this.windup = windup;
        this.damageMul = damageMul;
        this.up = up;
        this.fromWater = fromWater;
        this.effect = effect;
        range(min, max);
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        if (!super.canStart(f, target)) return false;
        return fromWater ? f.inWater() : f.mob().onGround();
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        landed = false;
        done = false;
        return windup + 40;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        if (t < windup) {
            f.freeze();
            f.face(target);
            if (fromWater) f.particles(ParticleTypes.BUBBLE_COLUMN_UP, m.getX(), m.getY() + 0.5, m.getZ(), 4, 0.6, 0.3, 0.6, 0.05);
            return;
        }
        if (t == windup) {
            Vec3 d = new Vec3(target.getX() - m.getX(), 0, target.getZ() - m.getZ());
            double dist = d.length();
            d = d.normalize();
            double h = Math.min(2.2, 0.35 + dist * 0.11);
            m.setDeltaMovement(d.x * h, up + (target.getY() - m.getY()) * 0.06, d.z * h);
            m.hurtMarked = true;
            f.sound(fromWater ? SoundEvents.GENERIC_SPLASH : SoundEvents.RAVAGER_ATTACK, 1.5f, 0.9f);
            if (fromWater) f.particles(ParticleTypes.SPLASH, m.getX(), m.getY() + 1, m.getZ(), 60, 1, 0.5, 1, 0.3);
            return;
        }
        if (done) {
            f.finish();
            return;
        }
        m.getNavigation().stop();
        if (f.gap(target) < 0.8 && Math.abs(target.getY() - m.getY()) < m.getBbHeight() + 1) {
            m.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            if (f.hurt(target, (float) (f.attackDamage() * damageMul))) {
                f.push(target, 0.5, 0.25);
                if (effect != null) f.effect(target, effect.get());
            }
            done = true;
        }
        if (t > windup + 4 && (m.onGround() || (!fromWater && m.isInWater()) || (fromWater && t > windup + 8 && f.inWater()))) {
            if (!landed) {
                landed = true;
                f.groundRing(m.getBbWidth() * 0.6, 10);
            }
            done = true;
        }
    }
}
