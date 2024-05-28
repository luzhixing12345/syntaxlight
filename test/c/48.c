for (uint32_t i = 0; i < group_count; i++) {
    INFO("group [%d] block bitmap[%lu], inode bitmap[%lu], inode table[%lu-%lu]",
         i,
         d_bitmap_start + i,
         i_bitmap_start + i,
         inode_table_start + i * inode_table_len,
         inode_table_start + (i + 1) * inode_table_len - 1);
    // ...
    uint64_t free_blocks_count = MKFS_EXT4_GROUP_BLOCK_CNT;
    uint64_t free_inode_count = sb.s_inodes_per_group;
    // calculate left free block count
    if (i == group_count - 1) {
        free_blocks_count = block_count - (group_count - 1) * MKFS_EXT4_GROUP_BLOCK_CNT;
        free_inode_count = inode_count - (group_count - 1) * sb.s_inodes_per_group;
    } else if (i == 0) {
        free_blocks_count--;  // root data block
        free_inode_count--;   // root inode
    }
    // ...
}