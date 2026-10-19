package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;

/**
 * Passive: while it circles from a distance the hunter is invisible (and quicker); it shows itself when it comes
 * close, and for a few seconds after it is hurt.
 */
public class Stalk extends Ability {
    private final double revealRange;
    private int revealed;
    private float lastDamage;

    public Stalk(double revealRange) {
        super(0);
        this.revealRange = revealRange;
    }

    @Override
    public boolean passive() {
        return true;
    }

    @Override
    public void passiveTick(BossFight f, LivingEntity target) {
        if (f.damageTaken() > lastDamage) {
            lastDamage = f.damageTaken();
            revealed = 80;
        }
        if (revealed > 0) revealed--;
        boolean hide = target != null && revealed == 0 && !f.busy() && f.mob().distanceTo(target) > revealRange;
        if (hide) {
            f.mob().addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 15, 0, false, false, false));
            f.mob().addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 15, 0, false, false, false));
        } else if (f.mob().hasEffect(MobEffects.INVISIBILITY)) {
            f.mob().removeEffect(MobEffects.INVISIBILITY);
        }
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return 0;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
    }
}
