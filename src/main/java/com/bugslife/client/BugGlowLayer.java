package com.bugslife.client;

import com.bugslife.entity.BugEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.texture.AutoGlowingTexture;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/** Full-bright glowmask layer whose brightness follows {@link BugEntity#glowStrength} (fireflies flash in sync). */
public class BugGlowLayer extends GeoRenderLayer<BugEntity> {
    public BugGlowLayer(GeoRenderer<BugEntity> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, BugEntity bug, BakedGeoModel bakedModel, RenderType renderType, MultiBufferSource bufferSource,
                       VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (bug.isInvisible()) return;
        float strength = bug.glowStrength(partialTick);
        if (strength <= 0f) return;
        RenderType glow = AutoGlowingTexture.getRenderType(getTextureResource(bug));
        // GeckoLib cuts the glowing pixels out of the base texture, so this layer is the only thing drawing them:
        // dim it by darkening rather than fading, and never below a floor, or the lantern would vanish by day
        float light = 0.35f + 0.65f * Math.min(1f, strength);
        int base = getRenderer().getRenderColor(bug, partialTick, packedLight).argbInt();
        int r = (int) (((base >> 16) & 0xFF) * light);
        int g = (int) (((base >> 8) & 0xFF) * light);
        int b = (int) ((base & 0xFF) * light);
        int argb = 0xFF000000 | (r << 16) | (g << 8) | b;
        getRenderer().reRender(bakedModel, poseStack, bufferSource, bug, glow, bufferSource.getBuffer(glow), partialTick,
                LightTexture.FULL_BRIGHT, packedOverlay, argb);
    }
}
