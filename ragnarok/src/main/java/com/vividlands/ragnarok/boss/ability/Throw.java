package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.Boulder;
import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;

/** Tears up a boulder and hurls it (several, quickly, once enraged). */
public class Throw extends Ability {
    private final int windup, count, gap;
    private final double damageMul;

    public Throw(int cooldown, int windup, int count, int gap, double damageMul) {
        super(cooldown);
        this.windup = windup;
        this.count = count;
        this.gap = gap;
        this.damageMul = damageMul;
        range(5, 30);
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return super.canStart(f, target) && f.mob().hasLineOfSight(target);
    }

    private int throwsNow(BossFight f) {
        return f.enraged() ? count + 1 : count;
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        return windup + throwsNow(f) * gap + 5;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t == 0) f.groundRing(f.mob().getBbWidth() * 0.6, 12);
        if (t >= windup && (t - windup) % gap == 0 && (t - windup) / gap < throwsNow(f)) {
            Mob m = f.mob();
            m.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            Boulder b = new Boulder(f.level(), m, (float) (f.attackDamage() * damageMul));
            b.setPos(m.getX(), m.getY() + m.getBbHeight() * 0.9, m.getZ());
            double dx = target.getX() - b.getX(), dz = target.getZ() - b.getZ();
            double dy = target.getY(0.4) - b.getY();
            double dist = Math.sqrt(dx * dx + dz * dz);
            b.shoot(dx, dy + dist * 0.18, dz, 1.25f, 3f);
            f.level().addFreshEntity(b);
            f.sound(SoundEvents.SNOWBALL_THROW, 1.5f, 0.4f);
        }
    }
}
