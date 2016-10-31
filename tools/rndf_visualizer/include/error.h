/*
 *  Description:  ROS log message wrappers.
 *
 *  This depends on some GCC macro preprocessor extensions for
 *  variable numbers of arguments that may not be available on every
 *  system.
 *
 *  Copyright (C) 2009 Austin Robot Technology, Jack O'Quin
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: 9d713b1a933668f1c5d8cb09e0306f996dbe52d6 $
 */

#ifndef ART_ERROR_H
#define ART_ERROR_H

/**  @file
   
     @brief ROS wrappers for ART error logging
 */

/* make this header bilingual */
#ifdef __cplusplus
extern "C" {
#endif

/* error, warning and informational message macros */
#define ART_ERROR(msg,args...) ROS_ERROR("error   : " msg, ## args)
#define ART_WARN(msg,args...)  ROS_WARN("warning : " msg, ## args)
#define ART_MSG(level, msg,args...)  ROS_INFO(msg, ## args)

#ifdef __cplusplus
}
#endif

#endif // ART_ERROR_H
