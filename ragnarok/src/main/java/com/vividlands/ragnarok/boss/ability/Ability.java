package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import net.minecraft.world.entity.LivingEntity;

/**
 * A boss special move. The fight runs one at a time: {@link #start} returns how many ticks it lasts, {@link #tick}
 * is called every tick until then, and the move can't be used again until its cooldown is over.
 * A move that is passive ({@link #passive}) never starts; its {@link #passiveTick} runs every tick instead.
 */
public abstract class Ability {
    protected final int cooldown;
    protected double minRange = 0, maxRange = 24;

    protected Ability(int cooldown) {
        this.cooldown = cooldown;
    }

    public int cooldown() {
        return cooldown;
    }

    public Ability range(double min, double max) {
        this.minRange = min;
        this.maxRange = max;
        return this;
    }

    public boolean passive() {
        return false;
    }

    public void passiveTick(BossFight f, LivingEntity target) {
    }

    public boolean canStart(BossFight f, LivingEntity target) {
        double d = f.mob().distanceTo(target);
        return d >= minRange && d <= maxRange;
    }

    /** @return duration in ticks */
    public abstract int start(BossFight f, LivingEntity target);

    public abstract void tick(BossFight f, LivingEntity target, int t);

    public void end(BossFight f) {
    }
}
