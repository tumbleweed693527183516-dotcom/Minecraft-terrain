package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * Tucks in and spins (shell, tail or whole body), rolling after you and hitting everything around it. Afterwards it
 * is dizzy for a moment: that's your opening.
 */
public class Spin extends Ability {
    private final int windup, duration, dizzy;
    private final double radius, damageMul, speed;

    public Spin(int cooldown, int windup, int duration, double radius, double speed, double damageMul, int dizzy) {
        super(cooldown);
        this.windup = windup;
        this.duration = duration;
        this.radius = radius;
        this.speed = speed;
        this.damageMul = damageMul;
        this.dizzy = dizzy;
        range(0, 18);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.sound(SoundEvents.TURTLE_SHAMBLE, 1.5f, 0.5f);
        return windup + duration;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        if (t < windup) {
            f.freeze();
            f.face(target);
            if (t % 3 == 0) f.marker(f.groundAt(m.getX(), m.getY(), m.getZ()), radius, BossFight.DANGER);
            return;
        }
        float yaw = m.getYRot() + 36f;
        m.setYRot(yaw);
        m.setYBodyRot(yaw);
        Vec3 d = new Vec3(target.getX() - m.getX(), 0, target.getZ() - m.getZ());
        if (d.lengthSqr() > 1) d = d.normalize().scale(speed * (f.enraged() ? 1.2 : 1));
        else d = Vec3.ZERO;
        m.getNavigation().stop();
        m.setDeltaMovement(d.x, m.getDeltaMovement().y, d.z);
        if (t % 4 == 0) {
            f.groundRing(radius * 0.8, 10);
            f.sound(SoundEvents.PLAYER_ATTACK_SWEEP, 1f, 0.5f);
        }
        if (t % 8 == 0) {
            for (LivingEntity e : f.victims(radius)) {
                if (f.hurt(e, (float) (f.attackDamage() * damageMul))) f.push(e, 1.2, 0.35);
            }
        }
        if (t == windup + duration - 1 && dizzy > 0) {
            f.sound(SoundEvents.RAVAGER_STUNNED, 1.5f, 1.0f);
            f.stun(dizzy);
        }
    }
}
