package com.vividlands.ragnarok.armor;

import net.minecraft.ChatFormatting;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.RenderProvider;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoArmorRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;

/** A piece of ancient-civilization armor, drawn with its 3D GeckoLib model (geo/item/armor/<set>.geo.json). */
public class AncientArmorItem extends ArmorItem implements GeoItem {
    private final AncientArmorMaterial material;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

    public AncientArmorItem(AncientArmorMaterial material, Type type, Properties properties) {
        super(material, type, properties);
        this.material = material;
    }

    public AncientArmorMaterial ancientMaterial() {
        return material;
    }

    @Override
    public void createRenderer(Consumer<Object> consumer) {
        String id = material.set().id();
        consumer.accept(new RenderProvider() {
            private GeoArmorRenderer<AncientArmorItem> renderer;

            @Override
            public HumanoidModel<LivingEntity> getHumanoidArmorModel(LivingEntity entity, ItemStack stack, EquipmentSlot slot,
                                                                     HumanoidModel<LivingEntity> original) {
                if (this.renderer == null) {
                    this.renderer = new GeoArmorRenderer<>(new DefaultedItemGeoModel<>(new ResourceLocation("vividlands_ragnarok", "armor/" + id)));
                    // parts that glow in the dark (eyes, runes): textures/item/armor/<set>_glow.png, when the set has one.
                    // (GeckoLib's auto-glowing layer cuts those pixels out of the base texture, and on armour the glow pass
                    // never showed, leaving black holes; the fullbright layer the Jarl helm uses works.)
                    ResourceLocation glow = new ResourceLocation("vividlands_ragnarok", "textures/item/armor/" + id + "_glow.png");
                    if (net.minecraft.client.Minecraft.getInstance().getResourceManager().getResource(glow).isPresent()) {
                        this.renderer.addRenderLayer(new com.vividlands.ragnarok.weapon.FullbrightLayer<>(this.renderer, glow));
                    }
                }
                this.renderer.prepForRender(entity, stack, slot, original);
                return this.renderer;
            }
        });
    }

    @Override
    public Supplier<Object> getRenderProvider() {
        return renderProvider;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.vividlands_ragnarok.ancient." + material.set().id()).withStyle(ChatFormatting.GOLD));
    }
}
