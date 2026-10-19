package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.boss.BossHolder;
import com.vividlands.ragnarok.boss.Bosses;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientEntityEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.world.entity.Entity;

/** Client side of the bosses: learns which entities are bosses (for their size) and draws thrown boulders. */
final class BossClient {
    /** Boss packets that arrived before their entity (some mods spawn entities with their own, later packet). */
    private static final java.util.Map<Integer, String> PENDING = new java.util.HashMap<>();

    private BossClient() {
    }

    static void init() {
        ClientEntityEvents.ENTITY_LOAD.register((e, level) -> {
            String boss = PENDING.remove(e.getId());
            if (boss != null) Bosses.markBoss(e, boss);
        });
        EntityRendererRegistry.register(Bosses.BOULDER, ctx -> new ThrownItemRenderer<>(ctx, 3.0f, true));
        ClientPlayNetworking.registerGlobalReceiver(Bosses.PACKET, (client, handler, buf, sender) -> {
            int id = buf.readVarInt();
            String boss = buf.readUtf();
            client.execute(() -> {
                if (client.level == null) return;
                Entity e = client.level.getEntity(id);
                if (e == null) {
                    if (PENDING.size() > 256) PENDING.clear();
                    PENDING.put(id, boss);
                    return;
                }
                if (e instanceof BossHolder) {
                    Bosses.markBoss(e, boss);
                    Bosses.debug("client: {} is boss {}, {}x{}, baby {}, scale {}", e.getType().getDescriptionId(), boss,
                            e.getBbWidth(), e.getBbHeight(), e instanceof net.minecraft.world.entity.LivingEntity l && l.isBaby(),
                            e instanceof net.minecraft.world.entity.LivingEntity l2 ? l2.getScale() : 1f);
                }
            });
        });
    }
}
