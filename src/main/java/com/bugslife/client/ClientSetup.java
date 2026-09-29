package com.bugslife.client;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugData;
import com.bugslife.bug.BugSpecies;
import com.bugslife.item.BugJarItem;
import com.bugslife.registry.ModBlockEntities;
import com.bugslife.registry.ModEntities;
import com.bugslife.registry.ModItems;
import net.minecraft.client.renderer.item.ItemProperties;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

@EventBusSubscriber(modid = BugsLife.MODID, value = Dist.CLIENT)
public final class ClientSetup {
    private ClientSetup() {
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        for (BugSpecies species : BugSpecies.values()) {
            event.registerEntityRenderer(ModEntities.get(species).get(), ctx -> new BugRenderer(ctx, species));
        }
        event.registerBlockEntityRenderer(ModBlockEntities.TERRARIUM.get(), TerrariumRenderer::new);
    }

    @SubscribeEvent
    public static void clientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            ItemProperties.register(ModItems.BUG_JAR.get(), BugsLife.id("species"), (stack, level, entity, seed) -> {
                BugData data = BugJarItem.getBug(stack);
                return data == null ? 0f : (data.species().ordinal() + 1) / 100f;
            });
            ItemProperties.register(ModItems.CHITIN_SHIELD.get(), net.minecraft.resources.ResourceLocation.withDefaultNamespace("blocking"),
                    (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack ? 1f : 0f);
        });
    }

    @SubscribeEvent
    public static void clientExtensions(net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent event) {
        event.registerItem(new net.neoforged.neoforge.client.extensions.common.IClientItemExtensions() {
            private ChitinShieldRenderer renderer;

            @Override
            public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                if (renderer == null) renderer = new ChitinShieldRenderer();
                return renderer;
            }
        }, ModItems.CHITIN_SHIELD.get());
    }
}
