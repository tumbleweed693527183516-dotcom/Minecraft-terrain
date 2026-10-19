package com.vividlands.ragnarok.boss;

import com.vividlands.ragnarok.boss.ability.Ability;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * One boss: which existing creature it is built on (another mod's mob, so its model and animations are used as they
 * are), its stats, its abilities, where it spawns and what it drops. Stats are placeholders, balanced later.
 */
public final class BossDef {
    /** How the boss fights up close. */
    public enum Melee {
        /** the creature's own attack goal (its own attack animations); only the damage is set */
        OWN,
        /** the pack's chase-and-bite goal (for creatures that don't fight on their own) */
        BOSS
    }

    public final String id;
    public final int chapter;
    public final List<String> entities = new ArrayList<>();      // first one that exists is used (mod mob, then fallbacks)
    float health = 200, damage = 8, armor = 4, speed = 1.0f, scale = 1.0f, reach = 1.2f, knockback = 0.6f;
    int attackInterval = 24;
    Melee melee = Melee.OWN;
    BossEvent.BossBarColor color = BossEvent.BossBarColor.RED;
    boolean aquatic;
    final List<Supplier<Ability>> abilities = new ArrayList<>();
    final List<Supplier<MobEffectInstance>> onHit = new ArrayList<>();
    final List<String[]> drops = new ArrayList<>();             // {item id, count}
    int xp = 200;
    // spawning
    final List<String> biomes = new ArrayList<>();               // biome ids, or #tags
    final List<String> structures = new ArrayList<>();           // spawns once per structure, when a player is inside it
    int requiresCount;                                           // number of other Chapter 1 bosses beaten first
    final List<String> requires = new ArrayList<>();             // specific bosses beaten first

    BossDef(String id, int chapter) {
        this.id = id;
        this.chapter = chapter;
    }

    public float health() { return health; }
    public float damage() { return damage; }
    public float scale() { return scale; }
    public float reach() { return reach; }
    public float knockback() { return knockback; }
    public int attackInterval() { return attackInterval; }
    public Melee melee() { return melee; }
    public boolean aquatic() { return aquatic; }
    public String nameKey() { return "boss.vividlands_ragnarok." + id; }

    // ---- builder-style setters (used in Bosses) ----
    BossDef on(String... entityIds) { entities.addAll(List.of(entityIds)); return this; }
    BossDef stats(float health, float damage, float armor) { this.health = health; this.damage = damage; this.armor = armor; return this; }
    BossDef speed(float s) { speed = s; return this; }
    BossDef scale(float s) { scale = s; return this; }
    BossDef reach(float r) { reach = r; return this; }
    BossDef knockback(float k) { knockback = k; return this; }
    BossDef interval(int ticks) { attackInterval = ticks; return this; }
    BossDef melee(Melee m) { melee = m; return this; }
    BossDef bar(BossEvent.BossBarColor c) { color = c; return this; }
    BossDef inSea() { aquatic = true; return this; }
    BossDef ability(Supplier<Ability> a) { abilities.add(a); return this; }
    BossDef onHit(Supplier<MobEffectInstance> e) { onHit.add(e); return this; }
    BossDef drop(String item, int count) { drops.add(new String[]{item, Integer.toString(count)}); return this; }
    BossDef xp(int x) { xp = x; return this; }
    BossDef biomes(String... b) { biomes.addAll(List.of(b)); return this; }
    BossDef structures(String... s) { structures.addAll(List.of(s)); return this; }
    BossDef after(int count) { requiresCount = count; return this; }
    BossDef after(String... ids) { requires.addAll(List.of(ids)); return this; }
}
