package com.bugslife.client;

import net.minecraft.client.Minecraft;

/** Client-only entry points called from common code behind an isClientSide check. */
public final class ClientHooks {
    private ClientHooks() {
    }

    public static void openFieldGuide() {
        Minecraft.getInstance().setScreen(new FieldGuideScreen());
    }
}
