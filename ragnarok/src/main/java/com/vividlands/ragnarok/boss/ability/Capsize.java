package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

/** Rams the boat (or ship) the target is in from below: the boat is smashed and the target thrown into the water. */
public class Capsize extends Ability {
    private final int windup;
    private final float boatDamage;

    public Capsize(int cooldown, int windup, float boatDamage) {
        super(cooldown);
        this.windup = windup;
        this.boatDamage = boatDamage;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return target.getVehicle() != null && f.mob().distanceTo(target.getVehicle()) < 8 + f.mob().getBbWidth();
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return windup + 8;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        Entity boat = target.getVehicle();
        if (boat == null) {
            f.finish();
            return;
        }
        f.face(boat);
        if (t < windup) {
            f.mob().getNavigation().moveTo(boat.getX(), boat.getY() - 1, boat.getZ(), 1.6);
            f.particles(ParticleTypes.BUBBLE_COLUMN_UP, boat.getX(), boat.getY(), boat.getZ(), 6, 1, 0.2, 1, 0.1);
            return;
        }
        if (t == windup) {
            f.sound(SoundEvents.ZOMBIE_BREAK_WOODEN_DOOR, 2f, 0.6f);
            f.particles(ParticleTypes.SPLASH, boat.getX(), boat.getY() + 0.5, boat.getZ(), 80, 1.5, 0.5, 1.5, 0.3);
            boat.hurt(f.mob().damageSources().mobAttack(f.mob()), boatDamage);
            for (Entity rider : boat.getPassengers()) {
                if (rider instanceof LivingEntity l) {
                    rider.stopRiding();
                    f.hurt(l, f.attackDamage() * 0.5f);
                    f.push(l, 0.6, 0.7);
                }
            }
        }
    }
}
