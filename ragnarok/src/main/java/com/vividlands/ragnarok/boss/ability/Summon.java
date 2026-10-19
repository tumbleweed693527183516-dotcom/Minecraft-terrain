package com.vividlands.ragnarok.boss.ability;

import com.vividlands.ragnarok.boss.BossFight;
import com.vividlands.ragnarok.boss.Bosses;
import net.minecraft.world.entity.LivingEntity;

/** Calls others of its kind to fight beside it (temporary: they leave when the boss dies). */
public class Summon extends Ability {
    private final int count, maxAlive;
    private final float health, damageMul;

    public Summon(int cooldown, int count, int maxAlive, float health, float damageMul) {
        super(cooldown);
        this.count = count;
        this.maxAlive = maxAlive;
        this.health = health;
        this.damageMul = damageMul;
    }

    @Override
    public boolean canStart(BossFight f, LivingEntity target) {
        return Bosses.minionCount(f) < maxAlive;
    }

    @Override
    public int start(BossFight f, LivingEntity target) {
        f.mob().playAmbientSound();
        return 30;
    }

    @Override
    public void tick(BossFight f, LivingEntity target, int t) {
        f.freeze();
        f.face(target);
        if (t == 20) {
            f.sound(net.minecraft.sounds.SoundEvents.RAID_HORN.value(), 1.2f, 1.4f);
            for (int i = 0; i < count && Bosses.minionCount(f) < maxAlive; i++) {
                Bosses.spawnMinion(f, health, f.attackDamage() * damageMul);
            }
        }
    }
}
