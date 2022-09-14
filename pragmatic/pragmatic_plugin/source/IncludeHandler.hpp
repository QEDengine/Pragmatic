
#include <memory>

#include <clang/Frontend/FrontendActions.h>
#include <clang/Frontend/CompilerInstance.h>

#include "Utility.hpp"
#include "Globals.hpp"

using namespace clang;

namespace QED { namespace Pragmatic
{
	class PragmaticPPCallbacks : public PPCallbacks
	{
		public:
		SourceManager& sm;
		PragmaticPPCallbacks(SourceManager& sm) : sm(sm) { }

		public:
		virtual void InclusionDirective
		(
			SourceLocation HashLoc,
			const Token &IncludeTok,
			StringRef FileName,
			bool IsAngled,
			CharSourceRange FilenameRange,
			Optional<FileEntryRef> File,
			StringRef SearchPath,
			StringRef RelativePath,
			const Module *Imported,
			SrcMgr::CharacteristicKind FileType
			) override
			{
				if (Imported == nullptr && FileType == SrcMgr::CharacteristicKind::C_User)
				{
					std::string path = TrunkateClangPath(HashLoc.printToString(sm));

					auto meta = QED::Pragmatic::GetJSON();
					bool found = false;
					for (auto& include : meta["Include"])
					{
						if (include.contains("Location") && include["Location"] == path)
						{
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
	};

	class PragmaticASTConsumer : public ASTConsumer
	{
		public:
		PragmaticASTConsumer(CompilerInstance &CI)
		{
			metaFilePath = GetMacroValue(CI.getPreprocessor(), "PRAGMATIC_FILE_PATH");
			CI.getPreprocessor().addPPCallbacks(std::make_unique<PragmaticPPCallbacks>(CI.getSourceManager()));
		}
	};

	class PragmaticASTAction : public PluginASTAction
	{
		public:
		virtual std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI, clang::StringRef InFile) override
		{
			return std::make_unique<PragmaticASTConsumer>(CI);
		}

		virtual void EndSourceFileAction() override
		{
			clang::ASTFrontendAction::EndSourceFileAction();
		}

		virtual bool ParseArgs(const CompilerInstance &CI, const std::vector<std::string> &arg) override
		{
			return true;
		}
		virtual PluginASTAction::ActionType getActionType() override
		{
			return AddAfterMainAction;
		}
	};
}} // namespace QED::Pragmatic