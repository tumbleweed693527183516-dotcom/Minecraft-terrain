package com.vividlands.ragnarok.weapon;

import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.RenderProvider;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;

/** Client-only: builds the GeckoLib item renderer for a weapon (only ever called from createRenderer on the client). */
final class WeaponRender {
    private WeaponRender() {
    }

    static <T extends Item & GeoItem> RenderProvider provider(String id, boolean glow) {
        return new RenderProvider() {
            private GeoItemRenderer<T> renderer;

            @Override
            public BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (this.renderer == null) {
                    this.renderer = new GeoItemRenderer<>(new DefaultedItemGeoModel<>(
                            new ResourceLocation("vividlands_ragnarok", "weapon/" + id)));
                    if (glow) {
                        this.renderer.addRenderLayer(new FullbrightLayer<>(this.renderer,
                                new ResourceLocation("vividlands_ragnarok", "textures/item/weapon/" + id + "_glow.png")));
                    }
                }
                return this.renderer;
            }
        };
    }
}
