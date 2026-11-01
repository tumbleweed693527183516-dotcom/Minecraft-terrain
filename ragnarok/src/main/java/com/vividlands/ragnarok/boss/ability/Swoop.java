package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

/**
 * A flyer climbs high, its shadow (a warning ring) locks onto where you stand, then it dives. Sidestep at the last
 * moment: if it hits the ground it is stunned for a moment.
 */
public class Swoop extends Ability {
    private final int climb;
    private final double height, radius, damageMul;
    private Vec3 spot;

    public Swoop(int cooldown, int climb, double height, double radius, double damageMul) {
        super(cooldown);
        this.climb = climb;
        this.height = height;
        this.radius = radius;
        this.damageMul = damageMul;
        range(4, 32);
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        spot = null;
        f.sound(SoundEvents.PHANTOM_SWOOP, 2f, 0.6f);
        return climb + 40;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Mob m = f.mob();
        m.getNavigation().stop();
        if (t < climb) {                                 // climb above the target
            Vec3 aim = target.position().add(0, height, 0).subtract(m.position());
            m.setDeltaMovement(aim.scale(0.08));
            f.face(target);
            if (t >= climb - 15) {
                if (spot == null) spot = f.groundAt(target.getX(), target.getY(), target.getZ());
                if (t % 3 == 0) f.marker(spot, radius, BossFight.DANGER);
            }
            return;
        }
        if (spot == null) spot = f.groundAt(target.getX(), target.getY(), target.getZ());
        Vec3 d = spot.subtract(m.position());
        if (d.length() < 1.5 || m.onGround() || m.verticalCollisionBelow) {
            f.sound(SoundEvents.GENERIC_EXPLODE, 1.2f, 0.9f);
            f.groundRing(radius, 18);
            for (LivingEntity e : f.victims(radius)) {
                if (f.hurt(e, (float) (f.attackDamage() * damageMul))) f.push(e, 1.2, 0.5);
            }
            f.stun(40);                                  // crashed: open to hits
            return;
        }
        m.setDeltaMovement(d.normalize().scale(1.4));
        float yaw = (float) Math.toDegrees(Math.atan2(d.z, d.x)) - 90f;
        m.setYRot(yaw);
        m.setYBodyRot(yaw);
        for (LivingEntity e : f.victims(0.5)) {
            if (f.hurt(e, (float) (f.attackDamage() * damageMul))) f.push(e, 1.4, 0.4);
        }
    }
}
