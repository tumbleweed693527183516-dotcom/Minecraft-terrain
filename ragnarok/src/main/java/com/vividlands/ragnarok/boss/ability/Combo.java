package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * An attack string: a few quick strikes, each with a short lunge, then a slower heavy finisher that knocks you
 * flying. Learn the rhythm: block or back off before the last hit.
 */
public class Combo extends Ability {
    private final int hits, gap, finisherWindup;
    private final double damageMul, finisherMul;

    public Combo(int cooldown, int hits, int gap, double damageMul, int finisherWindup, double finisherMul) {
        super(cooldown);
        this.hits = hits;
        this.gap = gap;
        this.damageMul = damageMul;
        this.finisherWindup = finisherWindup;
        this.finisherMul = finisherMul;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return f.gap(target) <= f.def().reach() + 2.5;
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return 6 + hits * gap + finisherWindup + 12;
    }

    private void lunge(BossFight f, LivingEntity target, double s) {
        Vec3 d = new Vec3(target.getX() - f.mob().getX(), 0, target.getZ() - f.mob().getZ());
        if (d.lengthSqr() > 1e-4) d = d.normalize().scale(s);
        f.mob().setDeltaMovement(d.x, f.mob().getDeltaMovement().y, d.z);
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.face(target);
        f.mob().getNavigation().stop();
        int finisherAt = 6 + hits * gap + finisherWindup;
        if (t >= 6 && t < 6 + hits * gap && (t - 6) % gap == 0) {
            f.animate("attack");
            lunge(f, target, 0.35);
            f.sound(SoundEvents.PLAYER_ATTACK_SWEEP, 1.2f, 0.6f + 0.1f * ((t - 6) / gap));
            if (f.gap(target) <= f.def().reach() + 0.6 && f.hurt(target, (float) (f.attackDamage() * damageMul))) {
                f.push(target, 0.3, 0.1);
            }
        } else if (t == 6 + hits * gap) {
            f.animate("combo");                          // the wind-up of the heavy finisher
            f.sound(SoundEvents.RAVAGER_ATTACK, 1.5f, 0.5f);
        } else if (t == finisherAt) {
            lunge(f, target, 0.6);
            f.sound(SoundEvents.GENERIC_EXPLODE, 1f, 0.7f);
            f.groundRing(f.def().reach() + 1, 14);
            if (f.gap(target) <= f.def().reach() + 1.2 && f.hurt(target, (float) (f.attackDamage() * finisherMul))) {
                f.push(target, 1.8, 0.6);
            }
        } else if (t > 6 + hits * gap && t < finisherAt) {
            f.freeze();
        }
    }
}
