
#include "BswNvm.h"
#include "NvM.h"


uint8 ShrHWIA_BswNvm_ReadBlock(uint8 index, uint8* data)
{
    uint8 status = 0U; // Initialize return status

    switch (index) {
        case BSWNVM_BLOCK_INDEX_0:
        	status = NvM_ReadBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_0, data);
            break;

        case BSWNVM_BLOCK_INDEX_1:
        	status = NvM_ReadBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_1, data);
            break;

        case BSWNVM_BLOCK_INDEX_2:
        	status = NvM_ReadBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_2, data);
            break;

        case BSWNVM_BLOCK_INDEX_3:
        	status = NvM_ReadBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_3, data);
            break;

        default:
            status = 1U; // Set error code
            break;
    }

    return status; // Return final status
}

uint8 ShrHWIA_BswNvm_WriteBlock(uint8 index, uint8* data)
{
    uint8 status = 0U; // Initialize return status

    switch (index) {
        case BSWNVM_BLOCK_INDEX_0:
        	status = NvM_WriteBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_0, data);
            break;

        case BSWNVM_BLOCK_INDEX_1:
        	status = NvM_WriteBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_1, data);
            break;

        case BSWNVM_BLOCK_INDEX_2:
        	status = NvM_WriteBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_2, data);
            break;

        case BSWNVM_BLOCK_INDEX_3:
        	status = NvM_WriteBlock(NvMConf_NvMBlockDescriptor_NvMBlockDescriptor_3, data);
            break;
        default:
            status = 1U; // Set error code
            break;
    }

    return status; // Return final status
}


