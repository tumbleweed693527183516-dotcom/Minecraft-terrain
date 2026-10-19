package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;

/** Grabs the target (trunk, tusks, horns) and hurls it high into the air; the fall does the rest. */
public class Fling extends Ability {
    private final int windup;
    private final double damageMul, up, away;

    public Fling(int cooldown, int windup, double damageMul, double up, double away) {
        super(cooldown);
        this.windup = windup;
        this.damageMul = damageMul;
        this.up = up;
        this.away = away;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return f.gap(target) <= f.def().reach() + 1.0;
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return windup + 10;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t == windup && f.gap(target) <= f.def().reach() + 1.5) {
            f.mob().swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            f.sound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.5f, 0.5f);
            if (f.hurt(target, (float) (f.attackDamage() * damageMul))) {
                target.setDeltaMovement(0, 0, 0);
                f.push(target, away, up);
            }
        }
    }
}
