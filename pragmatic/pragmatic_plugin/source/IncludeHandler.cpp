// Source header
#include "IncludeHandler.hpp"

// Standard library
#include <memory>

// Pragmatic plugin
#include "Utility.hpp"
#include "Globals.hpp"

namespace QED { namespace Pragmatic
{
	void IncludeCallbacks::InclusionDirective
		(
			clang::SourceLocation HashLoc,
			const clang::Token &IncludeTok,
			clang::StringRef FileName,
			bool IsAngled,
			clang::CharSourceRange FilenameRange,
			clang::Optional<clang::FileEntryRef> File,
			clang::StringRef SearchPath,
			clang::StringRef RelativePath,
			const clang::Module *Imported,
			clang::SrcMgr::CharacteristicKind FileType
		)
		{
			if (Imported == nullptr && FileType == clang::SrcMgr::CharacteristicKind::C_User)
			{
				std::string path = QED::Pragmatic::TrunkateClangPath(HashLoc.printToString(sourceManager));

				QED::Pragmatic::metaFilePath = QED::Pragmatic::GetMacroValue(preProcessor, "PRAGMATIC_FILE_PATH");
				auto meta = QED::Pragmatic::GetJSON();
				bool found = false;
				for (auto& include : meta["Include"])
				{
					if (include.contains("Location") && include["Location"] == path)
					{
						if (include.contains("Path") && std::find(include["Path"].begin(), include["Path"].end(), RelativePath) == include["Path"].end())
							include["Path"].push_back(RelativePath);
						found = true;
					}
				}
				if (!found)
				{
					meta["Include"].push_back({ { "Path", {} }, {"Location", path } });
					meta["Include"].at(meta["Include"].size() - 1)["Path"].push_back(RelativePath);
				}
				std::ofstream sourceJson(QED::Pragmatic::metaFilePath);
				sourceJson << std::setw(4) << meta;
			}
		}
}} // namespace QED::Pragmatic