package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.advancement.BugActionTrigger;
import com.bugslife.advancement.CatchBugTrigger;
import net.minecraft.advancements.CriterionTrigger;
import net.minecraft.core.registries.Registries;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModTriggers {
    public static final DeferredRegister<CriterionTrigger<?>> TRIGGERS = DeferredRegister.create(Registries.TRIGGER_TYPE, BugsLife.MODID);

    public static final DeferredHolder<CriterionTrigger<?>, CatchBugTrigger> CATCH_BUG = TRIGGERS.register("catch_bug", CatchBugTrigger::new);
    public static final DeferredHolder<CriterionTrigger<?>, BugActionTrigger> BUG_ACTION = TRIGGERS.register("bug_action", BugActionTrigger::new);

    private ModTriggers() {
    }
}
