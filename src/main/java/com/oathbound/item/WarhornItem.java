package com.oathbound.item;

import com.oathbound.entity.mob.SpectralHousecarlEntity;
import com.oathbound.registry.ModEntities;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/** Hrodgar's warhorn. Sound it and two spectral housecarls rise to fight at your side for forty seconds. */
public class WarhornItem extends Item {
    public static final int COOLDOWN = 1800;

    public WarhornItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.WARHORN.get(), SoundSource.PLAYERS, 3.0f, 1.0f);
            for (int i = 0; i < 2; i++) {
                SpectralHousecarlEntity h = ModEntities.SPECTRAL_HOUSECARL.get().create(server, EntitySpawnReason.MOB_SUMMONED);
                if (h == null) continue;
                double a = player.getYRot() * Math.PI / 180 + (i == 0 ? 1.2 : -1.2) + Math.PI / 2;
                Vec3 at = player.position().add(Math.cos(a) * 1.8, 0, Math.sin(a) * 1.8);
                h.snapTo(at.x, at.y, at.z, player.getYRot(), 0);
                h.makeAlly(player, 800);
                server.addFreshEntity(h);
                Vfx.burst(server, ModParticles.SPIRIT.get(), at.add(0, 1, 0), 40, 0.4, 0.08);
            }
            Vfx.ring(server, ModParticles.SPIRIT.get(), player.position().add(0, 0.2, 0), 3, 40, 0.05);
        }
        player.getCooldowns().addCooldown(stack, com.oathbound.event.GameEvents.cooldown(player, COOLDOWN));
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 2);
    }
}
