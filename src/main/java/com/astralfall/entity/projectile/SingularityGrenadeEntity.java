package com.astralfall.entity.projectile;

import com.astralfall.entity.SingularityEntity;
import com.astralfall.registry.ModEntities;
import com.astralfall.registry.ModItems;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Thrown Singularity Grenade: opens a black hole wherever it lands. */
public class SingularityGrenadeEntity extends ThrowableItemProjectile {
    public SingularityGrenadeEntity(EntityType<? extends SingularityGrenadeEntity> type, Level level) {
        super(type, level);
    }

    public SingularityGrenadeEntity(Level level, LivingEntity owner, ItemStack stack) {
        super(ModEntities.SINGULARITY_GRENADE.get(), owner, level, stack);
    }

    @Override
    protected Item getDefaultItem() {
        return ModItems.SINGULARITY_GRENADE.get();
    }

    @Override
    protected void onHit(HitResult hit) {
        super.onHit(hit);
        if (level() instanceof ServerLevel server) {
            Vec3 at = hit.getLocation().add(0, 1.2, 0);
            SingularityEntity.spawn(server, at, getOwner() instanceof LivingEntity l ? l : null, 70, 7.5f, 12.0f, false);
            discard();
        }
    }
}
