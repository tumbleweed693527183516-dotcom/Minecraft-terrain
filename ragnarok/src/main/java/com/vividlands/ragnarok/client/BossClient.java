package com.vividlands.ragnarok.client;

import com.vividlands.ragnarok.boss.BossHolder;
import com.vividlands.ragnarok.boss.Bosses;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.world.entity.Entity;

/** Client side of the bosses: learns which entities are bosses (for their size) and draws thrown boulders. */
final class BossClient {
    private BossClient() {
    }

    static void init() {
        EntityRendererRegistry.register(Bosses.BOULDER, ctx -> new ThrownItemRenderer<>(ctx, 3.0f, true));
        ClientPlayNetworking.registerGlobalReceiver(Bosses.PACKET, (client, handler, buf, sender) -> {
            int id = buf.readVarInt();
            String boss = buf.readUtf();
            client.execute(() -> {
                if (client.level == null) return;
                Entity e = client.level.getEntity(id);
                if (e instanceof BossHolder h) {
                    h.vlr$setBoss(boss);
                    e.refreshDimensions();
                }
            });
        });
    }
}
