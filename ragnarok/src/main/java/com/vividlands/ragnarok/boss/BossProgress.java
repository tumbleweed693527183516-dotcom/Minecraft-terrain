package com.vividlands.ragnarok.boss;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Saved with the world: which bosses each player has beaten (the story's progress), and where bosses have already
 * appeared (each wild boss appears once per region, each structure boss once per structure).
 */
public final class BossProgress extends SavedData {
    private static final String NAME = "vividlands_ragnarok_bosses";
    private final Map<UUID, Set<String>> defeated = new HashMap<>();
    private final Set<String> spawned = new HashSet<>();

    public static BossProgress get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(BossProgress::load, BossProgress::new, NAME);
    }

    private static BossProgress load(CompoundTag tag) {
        BossProgress p = new BossProgress();
        CompoundTag d = tag.getCompound("defeated");
        for (String k : d.getAllKeys()) {
            Set<String> set = new HashSet<>();
            for (Tag t : d.getList(k, Tag.TAG_STRING)) set.add(t.getAsString());
            try {
                p.defeated.put(UUID.fromString(k), set);
            } catch (IllegalArgumentException ignored) {
                // skip a broken entry
            }
        }
        for (Tag t : tag.getList("spawned", Tag.TAG_STRING)) p.spawned.add(t.getAsString());
        return p;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        CompoundTag d = new CompoundTag();
        defeated.forEach((u, set) -> {
            ListTag l = new ListTag();
            set.forEach(s -> l.add(StringTag.valueOf(s)));
            d.put(u.toString(), l);
        });
        tag.put("defeated", d);
        ListTag s = new ListTag();
        spawned.forEach(x -> s.add(StringTag.valueOf(x)));
        tag.put("spawned", s);
        return tag;
    }

    public Set<String> defeated(UUID player) {
        return defeated.getOrDefault(player, Set.of());
    }

    public void defeat(UUID player, String boss) {
        if (defeated.computeIfAbsent(player, k -> new HashSet<>()).add(boss)) setDirty();
    }

    public void forget(UUID player) {
        if (defeated.remove(player) != null) setDirty();
    }

    public boolean spawnedAt(String key) {
        return spawned.contains(key);
    }

    public void markSpawned(String key) {
        if (spawned.add(key)) setDirty();
    }

    public void clearSpawned() {
        spawned.clear();
        setDirty();
    }
}
