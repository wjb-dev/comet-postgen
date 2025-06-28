# def _purge_unrelated(self, root: Path, spec: PathSpec) -> None:
#     """
#     Walk the project tree; delete every path NOT matched by *spec*.
#
#     Updated to align with the `test_java_manifest` logic for cleaner organization.
#     """
#
#     # Dictionaries to separate matches and non-matches for logging
#
#     # 1) Dump every path under root or state what was found
#     all_paths = list(root.rglob("*"))
#     if self._log.evm:
#         self._log.debug(f"📋 All paths under {root} (total {len(all_paths)}):")
#         for p in all_paths:
#             print(f"{p.relative_to(root)}")
#     else:
#         self._log.debug(f"Found {len(all_paths)} paths under {root})")
#
#     matches, non_matched_files, directories_skipped, non_matched_dirs = [], [], [], []
#     for path in all_paths:
#         self._log.debug(f"\nScanning path: {path}")
#         rel = path.relative_to(root).as_posix()
#         self._log.debug(f"Relative path for inspection: {rel}")
#         # Match file against the PathSpec
#         if spec.match_file(rel):
#             self._log.debug(f"✅ KEEP: Path matches keep patterns: {rel}")
#             matches.append(path)  # Collect paths to keep
#         else:
#             if path.is_dir():
#                 if self._is_dir_protected(rel, spec):
#                     self._log.debug(f"{"⏭️ SKIPPING DELETE: Protected ancestor found: %s", path}")
#                     directories_skipped.append(rel)
#                 else:
#                     self._f.remove_dir(path)
#                     non_matched_dirs.append(rel)
#             else:
#                 non_matched_files.append(rel)
#                 self._f.remove_file(path)
#                 self._log.debug(f"{"❌ DELETE FILE: %s", rel}")
#
#         # Non-matching paths: collect and delete
#         self._log.debug(f"❌ DELETE: Path does not match keep patterns: {rel}")
#
#         if path.is_dir():
#             directories_skipped.append(path)
#             self._log.debug(f"⏭️ SKIPPING DELETE: Path is a directory: {path}")
#
#     # Print results cleanly for debugging/logging purposes
#     self._log.info("\nPATHS TO KEEP:")
#     self._log.info("=" * 80)
#     for match in matches:
#         self._log.info(f"✅ {match}")
#
#     self._log.info("\nPATHS TO PURGE:")
#     self._log.info("=" * 80)
#     for non_match in non_matched_files + non_matched_dirs:
#         self._log.info(f"❌ {non_match}")
#         self._f.remove_dir(non_match)