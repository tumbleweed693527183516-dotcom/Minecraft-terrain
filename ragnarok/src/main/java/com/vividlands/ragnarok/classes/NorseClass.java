package com.vividlands.ragnarok.classes;

import java.util.List;

/**
 * The five classes. Each has a passive and four abilities that unlock at levels 1, 10, 20 and 35; every number an
 * ability has grows in a straight line from level 1 to level 50 (see {@link #lerp}).
 */
public enum NorseClass {
    BERSERKER("berserker", "Berserker", 0xD0453A, "Battle Fury", "+1% melee damage per level",
            List.of(
                    new Ability("Bloodrage", 1, 30, "For 6 to 11 s: Strength, and your hits heal you for 10% to 30% of the damage."),
                    new Ability("Cleaving Leap", 10, 14, "Leap forward and crash down, dealing 6 to 21 damage around you."),
                    new Ability("Bear Shirt", 20, 45, "12 s of Resistance and 4 to 14 absorption hearts."),
                    new Ability("Undying Rage", 35, 300, "Passive once unlocked: a killing blow leaves you at 1 health and furious instead. Every 5 to 3 min."))),
    VALKYRIE("valkyrie", "Valkyrie", 0xE0B65A, "Wings of Asgard", "No fall damage; +0.1 armor per level",
            List.of(
                    new Ability("Spear of the Slain", 1, 6, "Hurl a spear of light up to 24 blocks: 5 to 20 damage to the first enemy."),
                    new Ability("Ascent", 10, 16, "Spring into the sky and glide down slowly."),
                    new Ability("Freyja's Aegis", 20, 40, "Shield yourself and allies within 10 blocks: 4 to 12 absorption hearts, cleanses poison and wither."),
                    new Ability("Choose the Slain", 35, 60, "Mark the enemy you look at for 10 s: it takes +25% to +50% damage from everyone; if it dies you heal."))),
    HUNTSMAN("huntsman", "Huntsman", 0x6FAF5A, "Skadi's Eye", "+1% arrow damage per level",
            List.of(
                    new Ability("Volley", 1, 10, "Loose a fan of 3 to 8 arrows."),
                    new Ability("Frost Snare", 10, 20, "Set a trap: the first enemies on it are frozen in place and take 4 to 14 damage."),
                    new Ability("Hunter's Mark", 20, 30, "Every enemy within 32 blocks glows for 10 s and takes +10% to +25% from your arrows."),
                    new Ability("Skadi's Hailstorm", 35, 60, "Arrows rain on the spot you look at for 5 s."))),
    VOLVA("volva", "Volva", 0x9A6AD8, "Seidr", "Ability cooldowns 0.5% shorter per level",
            List.of(
                    new Ability("Kenaz, the Torch", 1, 4, "A bolt of rune fire: 4 to 16 damage and sets the target alight."),
                    new Ability("Isa, the Ice", 10, 14, "A cone of frost: 3 to 13 damage and Slowness III."),
                    new Ability("Algiz, the Ward", 20, 35, "Regeneration II for you and allies within 8 blocks, for 5 to 10 s."),
                    new Ability("Thurisaz, the Thunder", 35, 45, "Lightning strikes 3 to 8 enemies near you for 8 to 28 damage."))),
    ULFHEDNAR("ulfhednar", "Ulfhednar", 0xB8C8D8, "Wolf Blood", "+0.4% movement speed per level",
            List.of(
                    new Ability("Call the Pack", 1, 40, "Summon 1 to 4 spirit wolves for 30 s."),
                    new Ability("Howl", 10, 25, "Enemies within 10 blocks are weakened and slowed; your wolves grow stronger."),
                    new Ability("Wolf Form", 20, 60, "For 14 to 24 s: Speed II, Jump Boost II, Strength and Night Vision."),
                    new Ability("Fenrir's Hunger", 35, 50, "For 8 s your hits make enemies bleed and heal you for 2 to 4 health.")));

    public static final int MAX_LEVEL = 50;

    public record Ability(String name, int unlock, int cooldownSeconds, String text) {
    }

    public final String id, title, passive, passiveText;
    public final int color;
    public final List<Ability> abilities;

    NorseClass(String id, String title, int color, String passive, String passiveText, List<Ability> abilities) {
        this.id = id;
        this.title = title;
        this.color = color;
        this.passive = passive;
        this.passiveText = passiveText;
        this.abilities = abilities;
    }

    public static NorseClass byId(String id) {
        for (NorseClass c : values()) if (c.id.equals(id)) return c;
        return null;
    }

    /** A value that grows in a straight line from {@code atOne} at level 1 to {@code atMax} at level 50. */
    public static double lerp(int level, double atOne, double atMax) {
        return atOne + (atMax - atOne) * (Math.max(1, Math.min(MAX_LEVEL, level)) - 1) / (double) (MAX_LEVEL - 1);
    }

    /** XP needed to go from {@code level} to the next: 100 at level 1, +25 per level. */
    public static int xpToNext(int level) {
        return 100 + 25 * (level - 1);
    }
}
