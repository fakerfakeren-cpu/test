package com.oathbound.entity.projectile;

import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ItemSupplier;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** The Drowned Anchor in flight. Yanks what it hits towards the thrower, or hauls the thrower to where it bites. */
public class AnchorHookEntity extends OathProjectile implements ItemSupplier {
    public AnchorHookEntity(EntityType<? extends AnchorHookEntity> type, Level level) {
        super(type, level);
        this.lifetime = 18;
        this.damage = 5.0f;
        this.gravity = 0.03f;
    }

    public AnchorHookEntity(Level level, LivingEntity owner) {
        this(ModEntities.ANCHOR_HOOK.get(), level);
        setOwner(owner);
    }

    @Override
    protected void strike(ServerLevel level, Entity hit) {
        dealDamage(level, hit, damage);
        Entity owner = getOwner();
        if (owner != null) {
            Vec3 pull = owner.position().subtract(hit.position());
            double d = pull.length();
            Vec3 v = pull.normalize().scale(Math.min(2.2, 0.35 + d * 0.16)).add(0, 0.35, 0);
            hit.setDeltaMovement(v);
            hit.hurtMarked = true;
        }
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ANCHOR_HIT.get(), SoundSource.PLAYERS, 1.2f, 1.0f);
        Vfx.burst(level, ModParticles.TIDE.get(), hit.getBoundingBox().getCenter(), 20, 0.4, 0.1);
        Vfx.burst(level, ParticleTypes.SPLASH, hit.getBoundingBox().getCenter(), 20, 0.4, 0.1);
    }

    @Override
    protected void impact(ServerLevel level, BlockHitResult hit) {
        Entity owner = getOwner();
        level.playSound(null, getX(), getY(), getZ(), ModSounds.ANCHOR_HIT.get(), SoundSource.PLAYERS, 1.2f, 0.7f);
        Vfx.burst(level, ModParticles.TIDE.get(), hit.getLocation(), 16, 0.3, 0.05);
        if (owner instanceof Player player) {
            Vec3 to = hit.getLocation().subtract(player.position());
            double d = to.length();
            Vec3 v = to.normalize().scale(Math.min(2.4, 0.5 + d * 0.15)).add(0, 0.45, 0);
            player.setDeltaMovement(v);
            player.hurtMarked = true;
            player.resetFallDistance();
        }
    }

    @Override
    protected void trail(Vec3 from, Vec3 to) {
        Entity owner = getOwner();
        if (owner == null) return;
        Vec3 hand = owner.position().add(0, owner.getBbHeight() * 0.65, 0);
        Vec3 d = to.subtract(hand);
        int n = (int) Math.max(2, d.length() * 2);
        for (int i = 0; i < n; i++) {
            Vec3 p = hand.add(d.scale(i / (double) n));
            level().addParticle(i % 2 == 0 ? ModParticles.TIDE.get() : ParticleTypes.BUBBLE_POP, p.x, p.y, p.z, 0, 0, 0);
        }
    }

    @Override
    public ItemStack getItem() {
        return new ItemStack(ModItems.DROWNED_ANCHOR.get());
    }
}
