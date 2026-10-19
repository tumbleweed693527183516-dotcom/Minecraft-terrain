package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;

/** A flurry of quick swipes or bites while the target is in reach. */
public class Maul extends Ability {
    private final int hits, interval;
    private final double damageMul;

    public Maul(int cooldown, int hits, int interval, double damageMul) {
        super(cooldown);
        this.hits = hits;
        this.interval = interval;
        this.damageMul = damageMul;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return f.gap(target) <= f.def().reach() + 0.5;
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return 8 + hits * interval;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.face(target);
        if (f.gap(target) > f.def().reach()) {
            f.mob().getNavigation().moveTo(target, 1.3);
        } else {
            f.freeze();
        }
        if (t >= 8 && (t - 8) % interval == 0) {
            f.mob().swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            f.sound(SoundEvents.PLAYER_ATTACK_SWEEP, 1f, 0.6f);
            if (f.gap(target) <= f.def().reach() + 0.4 && f.hurt(target, (float) (f.attackDamage() * damageMul))) {
                f.push(target, 0.25, 0.1);
            }
        }
    }
}
