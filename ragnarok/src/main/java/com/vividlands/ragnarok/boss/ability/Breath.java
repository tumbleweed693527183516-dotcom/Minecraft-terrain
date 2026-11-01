package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Breathes a cone (fire, frost, venom or Hel's shadow) that slowly sweeps after you. The mouth glows during the
 * wind-up; get behind it, or out of the cone, or behind a block.
 */
public class Breath extends Ability {
    public enum Kind {
        FIRE(ParticleTypes.FLAME, SoundEvents.BLAZE_SHOOT),
        FROST(ParticleTypes.SNOWFLAKE, SoundEvents.POWDER_SNOW_STEP),
        VENOM(ParticleTypes.SNEEZE, SoundEvents.SLIME_SQUISH),
        SHADOW(ParticleTypes.SOUL_FIRE_FLAME, SoundEvents.SOUL_ESCAPE);

        final ParticleOptions particle;
        final SoundEvent sound;

        Kind(ParticleOptions p, SoundEvent s) {
            particle = p;
            sound = s;
        }
    }

    private final int windup, duration;
    private final double length, halfAngle, damageMul;
    private final Kind kind;
    private float yaw;

    public Breath(int cooldown, int windup, int duration, double length, double angleDeg, double damageMul, Kind kind) {
        super(cooldown);
        this.windup = windup;
        this.duration = duration;
        this.length = length;
        this.halfAngle = Math.toRadians(angleDeg / 2);
        this.damageMul = damageMul;
        this.kind = kind;
        range(0, length * 0.8);
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return super.canStart(f, target) && f.mob().hasLineOfSight(target);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.face(target);
        yaw = f.mob().getYRot();
        f.sound(SoundEvents.ENDER_DRAGON_GROWL, 1.2f, 1.4f);
        return windup + duration;
    }

    private Vec3 mouth(Mob m) {
        double r = Math.toRadians(yaw);
        Vec3 fwd = new Vec3(-Math.sin(r), 0, Math.cos(r));
        return m.position().add(fwd.scale(m.getBbWidth() * 0.6)).add(0, m.getBbHeight() * 0.7, 0);
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        f.freeze();
        // the head turns after the target, but slowly: you can outrun the sweep
        double want = Math.toDegrees(Math.atan2(target.getZ() - m.getZ(), target.getX() - m.getX())) - 90;
        float diff = (float) net.minecraft.util.Mth.wrapDegrees(want - yaw);
        yaw += net.minecraft.util.Mth.clamp(diff, -2.5f, 2.5f);
        m.setYRot(yaw);
        m.setYBodyRot(yaw);
        m.setYHeadRot(yaw);
        Vec3 mo = mouth(m);
        if (t < windup) {
            if (t % 2 == 0) f.particles(kind.particle, mo.x, mo.y, mo.z, 3, 0.2, 0.2, 0.2, 0.01);
            return;
        }
        double r = Math.toRadians(yaw);
        Vec3 fwd = new Vec3(-Math.sin(r), -0.25, Math.cos(r)).normalize();
        for (int i = 0; i < 6; i++) {
            double d = 1 + m.getRandom().nextDouble() * length;
            double spread = d * Math.tan(halfAngle) * 0.8;
            f.particles(kind.particle, mo.x + fwd.x * d, mo.y + fwd.y * d, mo.z + fwd.z * d, 2, spread * 0.5, 0.3, spread * 0.5, 0.02);
        }
        if (t % 6 == 0) f.sound(kind.sound, 1.5f, 0.6f);
        if (t % 5 != 0) return;
        for (LivingEntity e : f.victims(length)) {
            Vec3 to = e.position().add(0, e.getBbHeight() * 0.5, 0).subtract(mo);
            double dist = to.length();
            if (dist > length + 1) continue;
            Vec3 flat = new Vec3(to.x, 0, to.z).normalize();
            double ang = Math.acos(Math.max(-1, Math.min(1, flat.x * -Math.sin(r) + flat.z * Math.cos(r))));
            if (ang > halfAngle || !e.hasLineOfSight(m)) continue;
            if (!f.hurt(e, (float) (f.attackDamage() * damageMul))) continue;
            switch (kind) {
                case FIRE -> e.setSecondsOnFire(4);
                case FROST -> {
                    e.setTicksFrozen(Math.min(e.getTicksRequiredToFreeze() + 60, e.getTicksFrozen() + 40));
                    f.effect(e, new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
                }
                case VENOM -> f.effect(e, new MobEffectInstance(MobEffects.POISON, 100, 1));
                case SHADOW -> f.effect(e, new MobEffectInstance(MobEffects.WITHER, 80, 0));
            }
        }
    }
}
