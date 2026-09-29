package com.bugslife.client;

import com.bugslife.BugsLife;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.ShieldModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/** Draws the chitin shield with the vanilla shield model and its own texture. */
public class ChitinShieldRenderer extends BlockEntityWithoutLevelRenderer {
    private static final ResourceLocation TEXTURE = BugsLife.id("textures/entity/chitin_shield.png");
    private ShieldModel model;

    public ChitinShieldRenderer() {
        super(Minecraft.getInstance().getBlockEntityRenderDispatcher(), Minecraft.getInstance().getEntityModels());
    }

    @Override
    public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack poseStack, MultiBufferSource buffer,
                             int packedLight, int packedOverlay) {
        if (model == null) {
            model = new ShieldModel(Minecraft.getInstance().getEntityModels().bakeLayer(ModelLayers.SHIELD));
        }
        poseStack.pushPose();
        poseStack.scale(1.0f, -1.0f, -1.0f);
        VertexConsumer consumer = ItemRenderer.getFoilBufferDirect(buffer, model.renderType(TEXTURE), true, stack.hasFoil());
        model.handle().render(poseStack, consumer, packedLight, packedOverlay);
        model.plate().render(poseStack, consumer, packedLight, packedOverlay);
        poseStack.popPose();
    }
}
