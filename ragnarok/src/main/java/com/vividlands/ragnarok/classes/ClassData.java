package com.vividlands.ragnarok.classes;

import net.minecraft.nbt.CompoundTag;

import java.util.EnumMap;
import java.util.Map;

/** One player's classes: the active one, XP in every class (switching back loses nothing) and ability cooldowns. */
public final class ClassData {
    public NorseClass active;
    public final Map<NorseClass, Integer> xp = new EnumMap<>(NorseClass.class);
    public final long[] readyAt = new long[4];          // game time each ability is ready again
    public long undyingReadyAt;
    public long switchReadyAt;

    public int totalXp(NorseClass c) {
        return xp.getOrDefault(c, 0);
    }

    public int level(NorseClass c) {
        int left = totalXp(c), level = 1;
        while (level < NorseClass.MAX_LEVEL && left >= NorseClass.xpToNext(level)) {
            left -= NorseClass.xpToNext(level);
            level++;
        }
        return level;
    }

    /** XP gained inside the current level (for the bar). */
    public int xpInLevel(NorseClass c) {
        int left = totalXp(c), level = 1;
        while (level < NorseClass.MAX_LEVEL && left >= NorseClass.xpToNext(level)) {
            left -= NorseClass.xpToNext(level);
            level++;
        }
        return left;
    }

    public int level() {
        return active == null ? 0 : level(active);
    }

    public void setLevel(NorseClass c, int level) {
        int total = 0;
        for (int l = 1; l < level; l++) total += NorseClass.xpToNext(l);
        xp.put(c, total);
    }

    public void copyFrom(ClassData o) {
        active = o.active;
        xp.clear();
        xp.putAll(o.xp);
        System.arraycopy(o.readyAt, 0, readyAt, 0, 4);
        undyingReadyAt = o.undyingReadyAt;
    }

    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        if (active != null) t.putString("active", active.id);
        CompoundTag x = new CompoundTag();
        xp.forEach((c, v) -> x.putInt(c.id, v));
        t.put("xp", x);
        return t;
    }

    public void load(CompoundTag t) {
        active = NorseClass.byId(t.getString("active"));
        xp.clear();
        CompoundTag x = t.getCompound("xp");
        for (NorseClass c : NorseClass.values()) if (x.contains(c.id)) xp.put(c, x.getInt(c.id));
    }
}
