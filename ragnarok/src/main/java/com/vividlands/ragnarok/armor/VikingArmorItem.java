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

/** A piece of Viking armor, drawn with its 3D GeckoLib model (geo/item/armor/<set>.geo.json). */
public class VikingArmorItem extends ArmorItem implements GeoItem {
    private final VikingArmorMaterial set;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final Supplier<Object> renderProvider = GeoItem.makeRenderer(this);

    public VikingArmorItem(VikingArmorMaterial set, Type type, Properties properties) {
        super(set, type, properties);
        this.set = set;
    }

    public VikingArmorMaterial set() {
        return set;
    }

    @Override
    public void createRenderer(Consumer<Object> consumer) {
        // Only called on the client (GeoItem.makeRenderer returns nothing on a dedicated server).
        consumer.accept(new RenderProvider() {
            private GeoArmorRenderer<VikingArmorItem> renderer;

            @Override
            public HumanoidModel<LivingEntity> getHumanoidArmorModel(LivingEntity entity, ItemStack stack, EquipmentSlot slot,
                                                                     HumanoidModel<LivingEntity> original) {
                if (this.renderer == null) {
                    this.renderer = new GeoArmorRenderer<>(new DefaultedItemGeoModel<>(
                            new ResourceLocation("vividlands_ragnarok", "armor/" + set.id())));
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
        tooltip.add(Component.translatable("tooltip.vividlands_ragnarok.set." + set.id()).withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.vividlands_ragnarok.bonus." + set.id())
                .withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.ITALIC));
    }
}
