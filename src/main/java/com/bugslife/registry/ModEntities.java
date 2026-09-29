package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.Map;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, BugsLife.MODID);

    private static final Map<BugSpecies, DeferredHolder<EntityType<?>, EntityType<BugEntity>>> TYPES = new EnumMap<>(BugSpecies.class);

    static {
        for (BugSpecies species : BugSpecies.values()) {
            TYPES.put(species, ENTITIES.register(species.id(), () -> {
                // MISC keeps bugs out of the vanilla mob caps; BugSpawner handles their spawning.
                EntityType.Builder<BugEntity> builder = EntityType.Builder.<BugEntity>of(BugEntity::new, MobCategory.MISC)
                        .sized(species.width(), species.height())
                        .clientTrackingRange(8)
                        .updateInterval(2);
                if (species.fireImmune()) {
                    builder.fireImmune();
                }
                EntityType<BugEntity> type = builder.build(BugsLife.MODID + ":" + species.id());
                BugSpecies.bindType(type, species);
                return type;
            }));
        }
    }

    public static DeferredHolder<EntityType<?>, EntityType<BugEntity>> get(BugSpecies species) {
        return TYPES.get(species);
    }

    private ModEntities() {
    }
}
