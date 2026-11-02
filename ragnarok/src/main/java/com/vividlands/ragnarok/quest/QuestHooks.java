package com.vividlands.ragnarok.quest;

import com.vividlands.ragnarok.Ragnarok;
import com.vividlands.ragnarok.classes.ClassData;
import com.vividlands.ragnarok.classes.NorseClass;
import net.minecraft.advancements.Advancement;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.StatFormatter;
import net.minecraft.stats.Stats;

/**
 * What the quest book (Odyssey Quests / Heracles) tracks from this mod: hidden advancements under
 * vividlands_ragnarok:quest/... (data/vividlands_ragnarok/advancements/quest, made by tools/questbook/build_quests.py)
 * and two custom statistics.
 */
public final class QuestHooks {
    private QuestHooks() {
    }

    public static final ResourceLocation BOSSES_KILLED = new ResourceLocation(Ragnarok.MOD_ID, "bosses_killed");
    public static final ResourceLocation BOSS_STAGGERS = new ResourceLocation(Ragnarok.MOD_ID, "boss_staggers");
    public static final int[] CLASS_LEVELS = {1, 5, 10, 20, 35, 50};

    public static void register() {
        for (ResourceLocation id : new ResourceLocation[]{BOSSES_KILLED, BOSS_STAGGERS}) {
            Registry.register(BuiltInRegistries.CUSTOM_STAT, id, id);
            Stats.CUSTOM.get(id, StatFormatter.DEFAULT);
        }
    }

    /** Grants vividlands_ragnarok:quest/<path> (no toast: the advancements have no display). */
    public static void award(ServerPlayer p, String path) {
        Advancement adv = p.server.getAdvancements().getAdvancement(new ResourceLocation(Ragnarok.MOD_ID, "quest/" + path));
        if (adv == null) return;
        var progress = p.getAdvancements().getOrStartProgress(adv);
        if (progress.isDone()) return;
        for (String c : progress.getRemainingCriteria()) p.getAdvancements().award(adv, c);
    }

    public static void stat(ServerPlayer p, ResourceLocation stat) {
        p.awardStat(stat);
    }

    /** Class level milestones, after any level change. */
    public static void classLevels(ServerPlayer p, ClassData d) {
        int at10 = 0, at20 = 0, best = 0;
        for (NorseClass c : NorseClass.values()) {
            int lv = d.level(c);
            if (d.xp.containsKey(c) || d.active == c) {
                for (int m : CLASS_LEVELS) if (lv >= m) award(p, "class/" + c.id + "_" + m);
            }
            if (lv >= 10) at10++;
            if (lv >= 20) at20++;
            best = Math.max(best, lv);
        }
        if (best >= 5) award(p, "class/any_5");
        if (at10 >= 2) award(p, "class/two_10");
        if (at20 >= NorseClass.values().length) award(p, "class/all_20");
    }
}
