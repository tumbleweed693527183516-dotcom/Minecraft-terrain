package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Clamps its jaws on the target and rolls: the target is held in its mouth and hurt again and again. Hit the boss
 * hard enough to break free.
 */
public class DeathRoll extends Ability {
    private final int hold;
    private final double damageMul;
    private final float breakFree;
    private float startDamage;
    private boolean grabbed;

    public DeathRoll(int cooldown, int hold, double damageMul, float breakFreeFraction) {
        super(cooldown);
        this.hold = hold;
        this.damageMul = damageMul;
        this.breakFree = breakFreeFraction;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return f.gap(target) <= f.def().reach() + 0.3 && !target.isPassenger();
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        grabbed = false;
        startDamage = f.damageTaken();
        return 6 + hold;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        f.freeze();
        if (t < 6) {
            f.face(target);
            return;
        }
        if (t == 6) {
            if (f.gap(target) > f.def().reach() + 0.8) {
                f.finish();
                return;
            }
            grabbed = true;
            m.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            f.sound(SoundEvents.EVOKER_FANGS_ATTACK, 1.5f, 0.6f);
            f.hurt(target, (float) (f.attackDamage() * damageMul));
        }
        if (!grabbed) return;
        // hold the target in front of the jaws, rolling
        m.setYRot(m.getYRot() + 24f);
        m.setYBodyRot(m.getYRot());
        float yaw = (float) Math.toRadians(m.getYRot() - 24f);
        double reach = m.getBbWidth() * 0.5 + target.getBbWidth() * 0.5 + 0.2;
        Vec3 mouth = new Vec3(m.getX() - Math.sin(yaw) * reach, m.getY() + 0.2, m.getZ() + Math.cos(yaw) * reach);
        if (target instanceof ServerPlayer p) {
            p.connection.teleport(mouth.x, mouth.y, mouth.z, p.getYRot(), p.getXRot());
        } else {
            target.teleportTo(mouth.x, mouth.y, mouth.z);
        }
        target.setDeltaMovement(Vec3.ZERO);
        target.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 80, 0, false, false, true));
        f.particles(f.inWater() ? ParticleTypes.BUBBLE : ParticleTypes.SPLASH, m.getX(), m.getY() + 0.5, m.getZ(), 6, 0.8, 0.3, 0.8, 0.05);
        if ((t - 6) % 10 == 9) f.hurt(target, (float) (f.attackDamage() * damageMul * 0.35));
        if (f.damageTaken() - startDamage >= m.getMaxHealth() * breakFree) {
            f.sound(SoundEvents.SHIELD_BREAK, 1.5f, 0.8f);
            f.push(target, 0.9, 0.4);
            f.stun(30);
        }
    }
}
